using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Text.Json;

namespace Converto_IT008_WPF.Api;

public class RemoveBackgroundApi : IRemoveBackgroundApi
{
    HttpClient _httpClient;
    SessionState _sessionState;
    string baseURL = App.AppConfig.BaseURL;

    public RemoveBackgroundApi(HttpClient httpClient, SessionState sessionState)
    {
        _httpClient = httpClient;
        _sessionState = sessionState;
    }

    public async Task<byte[]> RemoveBackgroundAsync(string[] filepaths)
    {
        try
        {
            string jsonPayload = JsonSerializer.Serialize(new {input_paths = filepaths });
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            string token = _sessionState.LoginResponse.access_token;

            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
            using HttpResponseMessage response = await _httpClient.PostAsync($"{baseURL}/remove_background", content);

            if (response.IsSuccessStatusCode)
            {
                byte[] result = await response.Content.ReadAsByteArrayAsync();
                return result;
            }
            else
            {
                string errorContent = await response.Content.ReadAsStringAsync();
                throw new Exception($"API Error: {response.StatusCode}, Content: {errorContent}");
            }
        }
        catch (Exception ex)
        {
            throw new Exception($"Error in RemoveBackgroundAsync: {ex.Message}");
        }
    }
}
