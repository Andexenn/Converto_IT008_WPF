using Converto_IT008_WPF.ViewModels;
using Converto_IT008_WPF.ViewModels.UserViewModel;
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
using System.Windows.Shapes;

namespace Converto_IT008_WPF.Views;

/// <summary>
/// Interaction logic for ConvertView.xaml
/// </summary>
public partial class ConvertView : UserControl
{
    public ConvertView()
    {
        InitializeComponent();
        DataContext = App.ServiceProvider?.GetRequiredService<ConvertViewModel>();
    }

    private void FileDrop(object sender, DragEventArgs e)
    {
        ResetUploadZoneVisual();
    }

    private void File_DragEnter(object sender, DragEventArgs e)
    {
        if (e.Data.GetDataPresent(DataFormats.FileDrop))
        {
            if (UploadZoneBackground != null)
            {
                UploadZoneBackground.Background = (Brush)FindResource("Brush.BG.Card");
            }

            //if (UploadZoneBorder != null)
            //{
            //    UploadZoneBorder.Stroke = Brushes.White;
            //    UploadZoneBorder.Opacity = 1.0;
            //}
        }
    }

    private void File_DragLeave(object sender, DragEventArgs e)
    {
        ResetUploadZoneVisual();
    }

    private void ResetUploadZoneVisual()
    {
        if (UploadZoneBackground != null)
        {
            UploadZoneBackground.Background = (Brush)FindResource("Color.Bg");
        }

        //if (UploadZoneBorder != null)
        //{
        //    UploadZoneBorder.Stroke = (Brush)FindResource("Brush.Text.Secondary");
        //    UploadZoneBorder.Opacity = 0.5;
        //}
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

    private bool AllowDrop(string[] filepaths)
    {
        string[] imgAllowExt = { ".jpg", ".png", ".webp", ".jpeg", ".tiff", ".bmp" };
        string[] videoAllowExt = { ".mp4", ".webm", ".mov", ".avi", ".mkv", ".aac" };
        string[] audioAllowExt = { ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a" };
        string[] documentAllowExt = { ".docx", ".xlsx", ".pptx" };

        string[] allowExt = imgAllowExt.Concat(videoAllowExt).Concat(audioAllowExt).ToArray();

        if (ComboboxTypeFormat != null && ComboboxTypeFormat.SelectedItem != null)
        {
            string type = ComboboxTypeFormat.SelectedItem.ToString();
            if (type.Contains("Image")) allowExt = imgAllowExt;
            else if (type.Contains("Video")) allowExt = videoAllowExt;
            else if (type.Contains("Audio")) allowExt = audioAllowExt;
            else if (type.Contains("Document")) allowExt = documentAllowExt;
        }

        foreach (var filepath in filepaths)
        {
            string ext = System.IO.Path.GetExtension(filepath).ToLower();
            if (!allowExt.Contains(ext)) return false;
        }
        return true;
    }
}
