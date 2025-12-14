using Converto_IT008_WPF.Dto;
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

    public async Task DeleteAccount()
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            using HttpResponseMessage response = await _httpClient.DeleteAsync($"{BaseURL}/user/delete_user");

            if (!response.IsSuccessStatusCode)
            {
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
            else
            {
                Debug.WriteLine("Account deleted successfully.");
            }
        }
        catch (Exception ex)
        {
            throw new ApplicationException("Error deleting account", ex);
        }
    }

    public async Task<UserInfo> SaveChanges(UserInfo userInfo)
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            var payload = System.Text.Json.JsonSerializer.Serialize(userInfo);
            var payloadContent = new StringContent(payload, Encoding.UTF8, "application/json");
            using HttpResponseMessage response = await _httpClient.PutAsync($"{BaseURL}/user/update_user_data", payloadContent);

            if(response.IsSuccessStatusCode)
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
            throw new ApplicationException("Error saving changes", ex);
        }
    }

    public async Task<bool> ChangePassword(string newPassword)
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            var payload = System.Text.Json.JsonSerializer.Serialize(new { new_password = newPassword });
            var payloadContent = new StringContent(payload, Encoding.UTF8, "application/json");
            using HttpResponseMessage response = await _httpClient.PutAsync($"{BaseURL}/user/change_password", payloadContent);
            if (response.IsSuccessStatusCode)
            {
                return true;
            }
            else
            {
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (Exception ex)
        {
            throw new ApplicationException("Error changing password", ex);
        }
    }

    public async Task<bool> UpdateUserPreference(UserPreferences userPreferences)
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            var payload = System.Text.Json.JsonSerializer.Serialize(userPreferences);
            var payloadContent = new StringContent(payload, Encoding.UTF8, "application/json");
            using HttpResponseMessage response = await _httpClient.PutAsync($"{BaseURL}/user/update_user_pref", payloadContent);
            if (response.IsSuccessStatusCode)
            {
                return true;
            }
            else
            {
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (Exception ex)
        {
            throw new ApplicationException("Error updating user preferences", ex);
        }
    }

    public async Task<bool> SendEmail(string emailType)
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            using HttpResponseMessage response = await _httpClient.GetAsync($"{BaseURL}/user/send_email/{emailType}");
            if (response.IsSuccessStatusCode)
            {
                return true;
            }
            else
            {
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (Exception ex)
        {
            throw new ApplicationException("Error sending email", ex);
        }
    }

    public async Task<bool> VerifyOTP(string otpCode)
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            var response = await _httpClient.GetAsync($"{BaseURL}/user/verify_otp/{otpCode}");
            if (response.IsSuccessStatusCode)
            {
                return true;
            }
            else
            {
                return false;
            }
        }
        catch (Exception ex)
        {
            throw new ApplicationException("Error verifying OTP", ex);
        }
    }
}
