using Accessibility;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.Stores;
using System;
using System.Buffers.Text;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Api;

public class ConvertApi : IConvertApi
{
    private readonly SessionState _sessionState;
    private readonly HttpClient _httpClient;
    private readonly string BaseURL = App.AppConfig.BaseURL;
    public ConvertApi(HttpClient httpClient, SessionState sessionState)
    {
        _httpClient = httpClient;
        _sessionState = sessionState;
    }

    public async Task<byte[]> ConvertFileAsync(string[] filepaths, string toFormat, string originalTypeFormat)
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            object payload = null;
            string endpoint = "";

            switch (originalTypeFormat.ToLower())
            {
                case "image":
                    payload = new { input_paths = filepaths, output_format = toFormat };
                    endpoint = "/convert_to/image";
                    break;
                case "video_audio":
                    payload = new { input_paths = filepaths, output_format = toFormat };
                    endpoint = "/convert_to/video_audio";
                    break;
                case "gif":
                    payload = new { input_paths = filepaths, output_format = toFormat };
                    endpoint = "/convert_to/gif";
                    break;
                case "pdf":
                    payload = new { input_paths = filepaths, output_format = toFormat };
                    endpoint = "/convert_to/pdf";
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
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (Exception ex)
        {
            throw new ApplicationException("Error converting file", ex);
        }
    }
}
