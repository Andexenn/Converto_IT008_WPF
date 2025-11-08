using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto.SignUpDto;

public class SignUpResponse
{
    public string Email { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string? Address { get; set; } = string.Empty;
    public string? City { get; set; } = string.Empty;
    public DateTime? DateOfBirth { get; set; }
    public string? PhoneNumber { get; set; } = string.Empty;
    public int UserID { get; set; }
}
