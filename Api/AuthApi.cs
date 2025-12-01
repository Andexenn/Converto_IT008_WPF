using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Dto.LoginDto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using Converto_IT008_WPF.Interfaces;

namespace Converto_IT008_WPF.Api;

public class AuthApi : IAuthApi
{
    private readonly HttpClient _httpClient;
    private const string BaseUrl = "http://localhost:5050/api/auth/";
    private string _accessToken = string.Empty;

    public AuthApi(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<SignUpResponse> SignUp(SignUpRequest signUpRequest)
    {
        try
        {
            var json = JsonSerializer.Serialize(signUpRequest);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            using HttpResponseMessage response = await _httpClient.PostAsync($"{BaseUrl}signup", content);

            if(response.IsSuccessStatusCode)
            {
                var reponseContent = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<SignUpResponse>(reponseContent);
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
            using HttpResponseMessage response = await _httpClient.GetAsync($"{BaseUrl}check-email/{Uri.EscapeDataString(Email)}");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var responseContent = JsonSerializer.Deserialize<CheckMailResponse>(json);
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
            var json = JsonSerializer.Serialize(loginRequest);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            using HttpResponseMessage response = await _httpClient.PostAsync($"{BaseUrl}login", content);

            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                var deserializedResponse = JsonSerializer.Deserialize<LoginResponse>(responseContent);
                _accessToken = deserializedResponse.access_token;
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
}
