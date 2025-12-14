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
    public void ProcessZipResponse(ObservableCollection<ProcessedFileResultDto> targetList, byte[] response);
    public void ProcessSingleImageResponse(ObservableCollection<ProcessedFileResultDto> targetList, byte[] response, string fileName, string ext, string typeService);
    public BitmapImage BytesToBitmap(byte[] data);
    public Task DownloadImages(ObservableCollection<ProcessedFileResultDto> processedImageResults, string customOutputPath = "");
}

