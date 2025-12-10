using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.Eventing.Reader;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Api;

public class UserApi : IUserApi
{
    HttpClient _httpClient;
    static readonly string BaseURL = App.AppConfig.BaseURL;
    SessionState _sessionState;
    public UserApi(HttpClient httpClient, SessionState sessionState)
    {
        _httpClient = httpClient;
        _sessionState = sessionState;
    }
    public async Task<UserPreferences> GetUserPreferencesAsync()
    {
        // Simulate an asynchronous API call
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            using HttpResponseMessage response = await _httpClient.GetAsync($"{BaseURL}/user/get_user_preference");
            if(response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var userPref = System.Text.Json.JsonSerializer.Deserialize<UserPreferences>(json);

                return userPref;
            }
            else
            {
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (Exception ex)
        {
            // Handle exceptions (e.g., log them)
            throw new ApplicationException("Error fetching user preferences", ex);
        }
    }

    public async Task<UserInfo> UpdateUserInfoAsync(UserInfo userInfo)
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);


            var options = new System.Text.Json.JsonSerializerOptions
            {
                // Quan trọng: Bỏ qua các trường có giá trị null
                DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull,

                // Đảm bảo không tự động đổi sang camelCase (nếu backend cần PascalCase)
                PropertyNamingPolicy = null
            };

            var jsonPayload = System.Text.Json.JsonSerializer.Serialize(userInfo, options);
            Debug.WriteLine("JSON gửi đi: " + jsonPayload);
            var jsonPayloadContent = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            using HttpResponseMessage response = await _httpClient.PutAsync($"{BaseURL}/user/update_user_data", jsonPayloadContent);

            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                return System.Text.Json.JsonSerializer.Deserialize<UserInfo>(json);
         
            }
            else
            {
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (Exception ex)
        {
            // Handle exceptions (e.g., log them)
            throw new ApplicationException("Error updating user info", ex);
        }
    }
}
