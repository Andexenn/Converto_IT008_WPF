using Converto_IT008_WPF.Interfaces.IUserApi;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
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

    public async Task<bool> SignUp(string FirstName, string LastName, string Email, string Password)
    {
        await Task.Delay(100);
        return true;
    }
}
