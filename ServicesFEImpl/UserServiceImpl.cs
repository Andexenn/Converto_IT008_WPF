using Converto_IT008_WPF.Dto;
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

    public async Task<UserPreferences> GetUserPreferencesAsync() => await _userApi.GetUserPreferencesAsync();
    

    public async Task<UserInfo> UpdateUserInfoAsync(UserInfo userInfo) => await _userApi.UpdateUserInfoAsync(userInfo);
    

    public async Task DeleteAccount() => await _userApi.DeleteAccount();
    
    public async Task<UserInfo> SaveChanges(UserInfo userInfo) => await _userApi.SaveChanges(userInfo);
    public async Task<bool> ChangePassword(string newPassword) => await _userApi.ChangePassword(newPassword);
    public async Task<bool> UpdateUserPreference(UserPreferences userPreferences) => await _userApi.UpdateUserPreference(userPreferences);
}
