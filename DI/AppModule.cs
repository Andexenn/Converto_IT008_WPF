using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.DI;

public static class AppModule
{
    public static IServiceCollection RegisterDependency(this IServiceCollection services)
    {
        services.AddTransient<Views.MainWindow>();

        return services;
    }
}
