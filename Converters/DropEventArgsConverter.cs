using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Windows;
using System.Windows.Data;

namespace Converto_IT008_WPF.Converters;

public class DropEventArgsConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        var args = value as DragEventArgs;
        if (args != null && args.Data.GetDataPresent(DataFormats.FileDrop))
            return args.Data.GetData(DataFormats.FileDrop) as string[];
        
        return null;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        throw new NotImplementedException();
    }
}
