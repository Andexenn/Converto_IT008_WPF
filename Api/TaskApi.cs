using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Api;

public class TaskApi : ITaskApi
{
    HttpClient _httpClient;
    private static readonly string BaseURL = App.AppConfig.BaseURL;
    SessionState _sessionState;
    public TaskApi(HttpClient httpClient, SessionState sessionState)
    {
        _httpClient = httpClient;
        _sessionState = sessionState;
    }

    public async Task<List<UserTasksDto>> GetUserTasksAsync()
    {
        try
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            using HttpResponseMessage response = await _httpClient.GetAsync($"{BaseURL}/task/task_by_user");
            if (response.IsSuccessStatusCode)
            {
                var json = await response.Content.ReadAsStringAsync();
                var userTasks = System.Text.Json.JsonSerializer.Deserialize<List<UserTasksDto>>(json);
                return userTasks;
            }
            else
            {
                throw new ApplicationException($"API Error: {response.StatusCode}, Content: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (Exception ex)
        {
            // Handle exceptions (e.g., log them)
            throw new ApplicationException("Error fetching user tasks", ex);
        }
    }
}
