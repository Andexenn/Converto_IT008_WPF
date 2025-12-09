using Converto_IT008_WPF.Dto;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ServicesFE;

public interface IProcessImageService
{
    public void ProcessZipResponse(ObservableCollection<ProcessedImageResult> targetList, byte[] response);
    public void ProcessSingleImageResponse(ObservableCollection<ProcessedImageResult> targetList, byte[] response);
    public BitmapImage BytesToBitmap(byte[] data);
}

