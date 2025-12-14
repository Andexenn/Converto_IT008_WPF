using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.Stores;
using Sprache;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Api;

public class CompressApi : ICompressApi
{
    SessionState _sessionState;
    HttpClient _httpClient;
    private readonly string BaseURL = App.AppConfig.BaseURL;
    public CompressApi(HttpClient httpClient, SessionState sessionState)
    {
        _httpClient = httpClient;
        _sessionState = sessionState;
    }

    public async Task<byte[]> CompressAsync(string[] filepaths, string typeFormat, string Quality = "low", string Bitrate = "64k")
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            object payload = null;
            string endpoint = "";

            switch (typeFormat.ToLower())
            {
                case "image":
                    int imgQuality = int.TryParse(Quality, out int q) ? q : 70;
                    payload = new { input_paths = filepaths, quality = imgQuality };
                    endpoint = "/compress/image";
                    break;
                case "audio":
                    payload = new { input_paths = filepaths, bitrate = Bitrate };
                    endpoint = "/compress/audio";
                    break;
                case "video":
                    payload = new { input_paths = filepaths, quality = Quality }; 
                    endpoint = "/compress/video";
                    break;
                default:
                    throw new ArgumentException("Invalid type format");
            }

            string jsonPayload = System.Text.Json.JsonSerializer.Serialize(payload);
            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{BaseURL}{endpoint}", content);

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
            throw new Exception("An error occurred while compressing files: " + ex.Message);
        }
    }
}
