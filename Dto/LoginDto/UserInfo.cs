using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto.LoginDto;

public class UserInfo
{
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string? Address { get; set; } = string.Empty;
    public string? City { get; set; } = string.Empty;
    public string? DateOfBirth { get; set; } = string.Empty;
    public string? PhoneNumber { get; set; } = string.Empty;
    public string? ProfilePictureURL { get; set; } = string.Empty;
    public DateTime? MemberSince { get; set; } = null;
    public DateTime? LastLogin { get; set; } = null;
}
