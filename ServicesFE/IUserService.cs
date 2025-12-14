using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Dto.LoginDto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFE;

public interface IUserService
{
    public Task<UserPreferences> GetUserPreferencesAsync();
    public Task<UserInfo> UpdateUserInfoAsync(UserInfo userInfo);
    public Task DeleteAccount();
    public Task<UserInfo> SaveChanges(UserInfo userInfo);
    public Task<bool> ChangePassword(string newPassword);
    public Task<bool> UpdateUserPreference(UserPreferences userPreferences);
    public Task<bool> SendEmail(string emailType);
    public Task<bool> VerifyOTP(string otpCode);
}
