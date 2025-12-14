using Converto_IT008_WPF.ViewModels.SideServices;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.IO;

namespace Converto_IT008_WPF.Views.ServiceViews;

/// <summary>
/// Interaction logic for CompressView.xaml
/// </summary>
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
            UploadZoneBackground.Opacity = 1.0;
            UploadZoneBackground.Background = (System.Windows.Media.Brush)FindResource("Brush.BG.Card");

            UploadZoneBorder.Stroke = System.Windows.Media.Brushes.White;
            UploadZoneBorder.Opacity = 1.0;
        }
    }

    private void File_DragLeave(object sender, DragEventArgs e)
    {
        ResetUploadZoneVisual();
    }

    private void ResetUploadZoneVisual()
    {
        UploadZoneBackground.Opacity = 0.5;
        UploadZoneBackground.Background = (System.Windows.Media.Brush)FindResource("Brush.BG.Shape");

        UploadZoneBorder.Stroke = (System.Windows.Media.Brush)FindResource("Brush.Text.Secondary");
        UploadZoneBorder.Opacity = 0.5;
    }

    private void File_Drop(object sender, DragEventArgs e)
    {
        ResetUploadZoneVisual();
    }

    private bool AllowDrop(string[] filepaths)
    {
        string[] imgAllowExt = { ".jpg", ".png", ".webp", ".jpeg", ".tiff", ".bmp" };
        string[] videoAllowExt = { ".mp4", ".webm", ".mov", ".avi", ".mkv", ".aac" };
        string[] audioAllowExt = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a" };
        string[] allowExt = { };

        if (ComboBoxTypeFormat.SelectedItem != null)
        {
            string type = ComboBoxTypeFormat.SelectedItem.ToString();
            if (type == "Image")
                allowExt = imgAllowExt;
            else if (type == "Video")
                allowExt = videoAllowExt;
            else if (type == "Audio")
                allowExt = audioAllowExt;
        }

        foreach (var filepath in filepaths)
        {
            string ext = Path.GetExtension(filepath).ToLower();

            if (!allowExt.Contains(ext))
                return false;
        }
        return true;
    }
}
