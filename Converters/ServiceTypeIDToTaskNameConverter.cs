using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Data;

namespace Converto_IT008_WPF.Converters;

public class ServiceTypeIDToTaskNameConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
    {
        if (value is int serviceTypeID)
        {
            return serviceTypeID switch
            {
                1 => "Conversion",
                2 => "Compression",
                3 => "Background Removal",
                _ => "Unknown Service"
            };
        }
        return "Unknown Service";
    }

    public object ConvertBack(object value, Type targetType, object parameter, System.Globalization.CultureInfo culture)
    {
        throw new NotImplementedException();
    }
}
