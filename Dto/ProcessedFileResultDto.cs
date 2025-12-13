using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.Dto;

public class ProcessedFileResultDto
{
    public string FileName { get; set; } = string.Empty;
    public BitmapImage DisplayImage { get; set; } = new BitmapImage();
    public byte[] RawData { get; set; } = Array.Empty<byte>();
}
