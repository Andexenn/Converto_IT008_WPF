using Converto_IT008_WPF.ViewModels.SideServices;
using Converto_IT008_WPF.ViewModels.UserViewModel;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Win32;
using System;
using System.Diagnostics.Eventing.Reader;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.Views.ServiceViews
{
    public partial class RemoveBackgroundView : UserControl
    {
        string[] filepaths = { };

        public RemoveBackgroundView()
        {
            InitializeComponent();
            DataContext = App.ServiceProvider?.GetRequiredService<RemoveBackgroundViewModel>();
        }

        private void Image_DragOver(object sender, DragEventArgs e)
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


        private void Image_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                UploadZoneBackground.Opacity = 1.0;
                UploadZoneBackground.Background = (System.Windows.Media.Brush)FindResource("Brush.BG.Card");

                UploadZoneBorder.Stroke = System.Windows.Media.Brushes.White;
                UploadZoneBorder.Opacity = 1.0;
            }
        }

        private void Image_DragLeave(object sender, DragEventArgs e)
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

        bool AllowDrop(string[] filepaths)
        {
            string[] allowExt = { ".jpg", ".png", ".webp", ".jpeg" };

            foreach (var filepath in filepaths)
            {
                string ext = Path.GetExtension(filepath).ToLower();

                if (!allowExt.Contains(ext))
                    return false ;

                
            }
            return true;
        }

    }
}