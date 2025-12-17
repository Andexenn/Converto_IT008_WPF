using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Data;

namespace Converto_IT008_WPF.Converters;

public class BytesToMegabytesConverter : IValueConverter
{

    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value == null) return "0 MB";

        if (double.TryParse(value.ToString(), out double bytes))
        {
            double megabytes = bytes / 1024.0 / 1024.0;

            return $"{megabytes:N2} MB";
        }

        return "0 MB";
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        throw new NotImplementedException();
    }
}
