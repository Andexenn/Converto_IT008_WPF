using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Dto;

public class OverviewDto
{
    public int TotalTasks { get; set; }
    public double StorageSave { get; set; }
    public double AvgProcessingTime { get; set; }
    public string SuccessRate { get; set; } = string.Empty;
}
