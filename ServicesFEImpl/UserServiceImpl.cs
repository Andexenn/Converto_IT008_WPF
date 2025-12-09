using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class UserServiceImpl : IUserService
{
    IUserApi _userApi;
    public UserServiceImpl(IUserApi userApi)
    {
        _userApi = userApi;
    }

    public async Task<UserPreferences> GetUserPreferencesAsync()
    {
        return await _userApi.GetUserPreferencesAsync();
    }

}
