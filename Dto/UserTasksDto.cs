using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto;

public class UserTasksDto
{
    public int ServiceTypeID { get; set; }
    public int OriginalFileSize { get; set; }
    public string? OriginalFilePath { get; set; } = string.Empty;
    public int? OutputFileSize { get; set; }
    public string? OutputFilePath { get; set; } = string.Empty;
    public bool TaskStatus { get; set; }
    public float TaskTime { get; set; }
    public DateTime CreatedAt { get; set; }
}
