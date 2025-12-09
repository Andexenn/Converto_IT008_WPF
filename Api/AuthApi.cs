using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Interfaces;
using Google.Apis.Auth.OAuth2;
using Google.Apis.Auth.OAuth2.Flows;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Security.Policy;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Converto_IT008_WPF.Helpers;

namespace Converto_IT008_WPF.Api;

public class AuthApi : IAuthApi
{
    private readonly HttpClient _httpClient;
    private static readonly string GoogleClientID = App.AppConfig.GoogleClientID;
    private static readonly string GoogleClientSecret = App.AppConfig.GoogleClientSecret;
    private static readonly string GithubClientID = App.AppConfig.GithubClientID;
    private static readonly string GithubClientSecret = App.AppConfig.GithubClientSecret;
    private static readonly string BaseURL = App.AppConfig.BaseURL;

    private readonly GoogleAuthorizationCodeFlow _flow;

    public AuthApi(HttpClient httpClient)
    {
        _httpClient = httpClient;


        _flow = new GoogleAuthorizationCodeFlow(new GoogleAuthorizationCodeFlow.Initializer
        {
            ClientSecrets = new ClientSecrets
            {
                ClientId = GoogleClientID,
                ClientSecret = GoogleClientSecret
            },
            Scopes = new[] { "openid", "email", "profile" }
        });
    }

    public async Task<SignUpResponse> SignUp(SignUpRequest signUpRequest)
    {
        try
        {
            var json = System.Text.Json.JsonSerializer.Serialize(signUpRequest);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            using HttpResponseMessage response = await _httpClient.PostAsync($"{BaseURL}/signup", content);

            if(response.IsSuccessStatusCode)
            {
                var reponseContent = await response.Content.ReadAsStringAsync();
                return System.Text.Json.JsonSerializer.Deserialize<SignUpResponse>(reponseContent);
            }
            else
            {
                var error = await response.Content.ReadAsStringAsync();
                throw new Exception($"Error during sign up: {error}");
            }
        }
        catch (Exception ex)
        {
            throw new Exception($"Exception in SignUp API: {ex.Message}");
        }
    }

    public async Task<bool> CheckMailExisting(string Email)
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.GetAsync($"{BaseURL}/auth/check-email/{Uri.EscapeDataString(Email)}");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var responseContent = System.Text.Json.JsonSerializer.Deserialize<CheckMailResponse>(json);
                return responseContent.exists;
            }
            else
            {
                var error = await response.Content.ReadAsStringAsync();
                throw new Exception($"Error during email check: {error}");
            }
        }
        catch (Exception ex)
        {
            throw new Exception($"Exception in CheckMailExisting API: {ex.Message}");
        }
    }

    public async Task<LoginResponse> Login(LoginRequest loginRequest)
    {
        try
        {
            var json = System.Text.Json.JsonSerializer.Serialize(loginRequest);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            using HttpResponseMessage response = await _httpClient.PostAsync($"{BaseURL}/auth/login", content);

            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                var deserializedResponse = System.Text.Json.JsonSerializer.Deserialize<LoginResponse>(responseContent);
                return deserializedResponse;
            }
            else
            {
                var error = await response.Content.ReadAsStringAsync();
                throw new Exception($"Error during login: {error}");
            }
        }
        catch (Exception ex)
        {
            throw new Exception($"Exception in Login API: {ex.Message}");
        }
    }

    public async Task<LoginResponse> SignInWithGoolge()
    {
        try
        {
            // Step 1: Start local HTTP listener for OAuth callback
            var redirectUri = "http://127.0.0.1:5000/";
            var httpListener = new HttpListener();
            httpListener.Prefixes.Add(redirectUri);
            httpListener.Start();

            // Step 2: Build authorization URL
            var authorizationUrl = _flow.CreateAuthorizationCodeRequest(redirectUri);
            authorizationUrl.ResponseType = "code";

            var authUrl = authorizationUrl.Build().ToString();

            // Step 3: Open browser for user to authenticate
            Process.Start(new ProcessStartInfo
            {
                FileName = authUrl,
                UseShellExecute = true
            });

            // Step 4: Wait for callback
            var context = await httpListener.GetContextAsync();
            var code = context.Request.QueryString.Get("code");

            // Send response to browser
            var responseString = "<html><body>Authentication successful! You can close this window.</body></html>";
            var buffer = Encoding.UTF8.GetBytes(responseString);
            context.Response.ContentLength64 = buffer.Length;
            await context.Response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
            context.Response.OutputStream.Close();
            httpListener.Stop();

            if (string.IsNullOrEmpty(code))
            {
                throw new Exception("Authorization code not received");
            }

            // Step 5: Exchange code for tokens
            var tokenResponse = await _flow.ExchangeCodeForTokenAsync(
                "user",
                code,
                redirectUri,
                System.Threading.CancellationToken.None
            );

            if(tokenResponse.RefreshToken != null)
                Cryptography.SaveRefreshToken(tokenResponse.RefreshToken);


            // Step 6: Get user info from ID token
            var payload = await Google.Apis.Auth.GoogleJsonWebSignature.ValidateAsync(
                tokenResponse.IdToken
            );

            // Step 7: Send to your backend
            var googleUserData = new
            {
                email = payload.Email,
                given_name = payload.GivenName,
                family_name = payload.FamilyName,
                picture = payload.Picture,
                id_token = tokenResponse.IdToken  // For backend verification
            };

            var json = JsonConvert.SerializeObject(googleUserData);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{BaseURL}/auth/google_login", content);
            var responseContent = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception($"Backend authentication failed: {responseContent}");
            }

            var loginResponse = JsonConvert.DeserializeObject<LoginResponse>(responseContent);

            return loginResponse;
        }
        catch (Exception ex)
        {
            throw new Exception($"Google Sign-In failed: {ex.Message}");
        }
    }

    public async Task<LoginResponse> SignInWithGithub()
    {
        try
        {
            var redirectUri = "http://127.0.0.1:5000/callback";

            using (var httpListener = new HttpListener())
            {
                httpListener.Prefixes.Add(redirectUri + "/");
                httpListener.Start();

                string state = Guid.NewGuid().ToString();
                string authUrl = $"https://github.com/login/oauth/authorize?client_id={GithubClientID}&redirect_uri={redirectUri}&scope=user:email&state={state}";

                Process.Start(new ProcessStartInfo
                {
                    FileName = authUrl,
                    UseShellExecute = true
                });

                var context = await httpListener.GetContextAsync();
                var request = context.Request;
                string code = request.QueryString.Get("code");
                string receivedState = request.QueryString.Get("state");

                string responseString = "<html><body style='font-family:sans-serif; text-align:center; margin-top:50px;'><h3>Login Successful!</h3><p>You can close this window and return to the application.</p><script>window.close();</script></body></html>";
                byte[] buffer = Encoding.UTF8.GetBytes(responseString);
                context.Response.ContentLength64 = buffer.Length;
                await context.Response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
                context.Response.OutputStream.Close();
                httpListener.Stop();

                if (string.IsNullOrEmpty(code) || receivedState != state)
                {
                    throw new Exception("Authorization failed or state mismatch.");
                }

                using (var httpClient = new HttpClient())
                {
                    var payload = new { code = code };
                    var json = JsonConvert.SerializeObject(payload);
                    var content = new StringContent(json, Encoding.UTF8, "application/json");

                    var response = await httpClient.PostAsync($"{BaseURL}/auth/github_login", content);

                    if (!response.IsSuccessStatusCode)
                    {
                        throw new Exception("Backend login failed.");
                    }

                    // Nhận JWT/Session từ FastAPI
                    var result = await response.Content.ReadAsStringAsync();
                    return JsonConvert.DeserializeObject<LoginResponse>(result);// Token của hệ thống bạn
                }
            }
        }
        catch (Exception ex)
        {
            throw new Exception($"GitHub Sign-In failed: {ex.Message}");
        }
    }
}
