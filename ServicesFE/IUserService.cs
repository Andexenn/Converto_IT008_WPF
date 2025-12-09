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
}
