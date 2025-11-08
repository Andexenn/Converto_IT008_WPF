using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Interfaces.IUserApi;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Api.UserApi;

public class AuthApi : IAuthApi
{
    private readonly HttpClient _httpClient;
    private const string BaseUrl = "http://localhost:8000/api/auth/";

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
}
