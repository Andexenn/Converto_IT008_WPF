using Converto_IT008_WPF.ViewModels.SideServices;
using Microsoft.Extensions.DependencyInjection;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace Converto_IT008_WPF.Views.ServiceViews;

public partial class CompressView : UserControl
{
    public CompressView()
    {
        InitializeComponent();
        DataContext = App.ServiceProvider?.GetRequiredService<CompressViewModel>();
    }

    private void File_DragOver(object sender, DragEventArgs e)
    {
        if (e.Data.GetDataPresent(DataFormats.FileDrop))
        {
            if (AllowDrop((string[])e.Data.GetData(DataFormats.FileDrop)))
                e.Effects = DragDropEffects.Copy;
            else
                e.Effects = DragDropEffects.None;
        }
        else
        {
            e.Effects = DragDropEffects.None;
        }
        e.Handled = true;
    }

    private void File_DragEnter(object sender, DragEventArgs e)
    {
        if (e.Data.GetDataPresent(DataFormats.FileDrop))
        {
            if (UploadZoneBackground != null)
            {
                UploadZoneBackground.Opacity = 1.0;
                UploadZoneBackground.Background = (Brush)FindResource("Brush.BG.Card");
            }

            if (UploadZoneBorder != null)
            {
                UploadZoneBorder.Stroke = Brushes.White;
                UploadZoneBorder.Opacity = 1.0;
            }
        }
    }

    private void File_DragLeave(object sender, DragEventArgs e)
    {
        ResetUploadZoneVisual();
    }

    private void File_Drop(object sender, DragEventArgs e)
    {
        ResetUploadZoneVisual();
    }

    private void ResetUploadZoneVisual()
    {
        if (UploadZoneBackground != null)
        {
            UploadZoneBackground.Opacity = 0.5;
            UploadZoneBackground.Background = (Brush)FindResource("Brush.BG.Shape");
        }

        if (UploadZoneBorder != null)
        {
            UploadZoneBorder.Stroke = (Brush)FindResource("Brush.Text.Secondary");
            UploadZoneBorder.Opacity = 0.5;
        }
    }

    private bool AllowDrop(string[] filepaths)
    {
        string[] imgAllowExt = { ".jpg", ".png", ".webp", ".jpeg", ".tiff", ".bmp" };
        string[] videoAllowExt = { ".mp4", ".webm", ".mov", ".avi", ".mkv", ".aac" };
        string[] audioAllowExt = { ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a" };

        string[] allowExt = imgAllowExt.Concat(videoAllowExt).Concat(audioAllowExt).ToArray();

        if (ComboBoxTypeFormat != null && ComboBoxTypeFormat.SelectedItem != null)
        {
            string type = ComboBoxTypeFormat.SelectedItem.ToString();
            if (type.Contains("Image")) allowExt = imgAllowExt;
            else if (type.Contains("Video")) allowExt = videoAllowExt;
            else if (type.Contains("Audio")) allowExt = audioAllowExt;
        }

        foreach (var filepath in filepaths)
        {
            string ext = Path.GetExtension(filepath).ToLower();
            if (!allowExt.Contains(ext)) return false;
        }
        return true;
    }
}