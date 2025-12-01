using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using Google.Apis.Auth.OAuth2;
using Google.Apis.Auth.OAuth2.Flows;
using Google.Apis.Auth.OAuth2.Responses;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class AuthServiceImpl : IAuthService
{
    private readonly IAuthApi _authApi;
    private const string ClientID = "922023715036-nf48f8o3rhm402a0q6p3nn9jfu420kbp.apps.googleusercontent.com";
    private const string ClientSecret = "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";   
    private const string BackendUrl = "http://localhost:5050/api/auth/google_login";

    private readonly HttpClient _httpClient;
    private readonly GoogleAuthorizationCodeFlow _flow;

    public AuthServiceImpl(IAuthApi authApi)
    {
        _authApi = authApi;
        _httpClient = new HttpClient();

        _flow = new GoogleAuthorizationCodeFlow(new GoogleAuthorizationCodeFlow.Initializer
        {
            ClientSecrets = new ClientSecrets
            {
                ClientId = ClientID,
                ClientSecret = ClientSecret
            },
            Scopes = new[] { "openid" ,"email", "profile" }
        });
    }
    public async Task<SignUpResponse> SignUp(SignUpRequest signUpRequest) => await _authApi.SignUp(signUpRequest);
    public async Task<bool> CheckMailExisting(string Email) => await _authApi.CheckMailExisting(Email);
    public async Task<LoginResponse> Login(LoginRequest loginRequest) => await _authApi.Login(loginRequest);

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

            var response = await _httpClient.PostAsync(BackendUrl, content);
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

}
