using System.Reflection;

namespace SSG.Shared;

public static class InterfaceDiscovery
{
    public static IEnumerable<Type> GetLoadableTypes(Assembly assembly)
    {
        if (assembly == null) return Enumerable.Empty<Type>();

        try
        {
            return assembly.GetTypes();
        }
        catch (ReflectionTypeLoadException e)
        {
            return (IEnumerable<Type>)e.Types.Where((Type? t) => t != null);
        }
    }

    public static IEnumerable<Type> GetImplementingTypes<I>(Assembly assembly) where I : class
    {
        var interfaceType = typeof(I);
        if (!interfaceType.IsInterface && !interfaceType.IsAbstract) return Enumerable.Empty<Type>();
        return GetLoadableTypes(assembly).Where(t => !t.Equals(interfaceType) && interfaceType.IsAssignableFrom(t)).ToList();
    }

    public static IEnumerable<Type> DiscoverImplementors<I>(params string[]? restrictToNamespaces) where I : class
    {
        if (!typeof(I).IsInterface && !typeof(I).IsAbstract) return Enumerable.Empty<Type>();

        IEnumerable<Type> retval = AppDomain.CurrentDomain.GetAssemblies()
            .SelectMany(assy => GetImplementingTypes<I>(assy))
            .Where(t => t != null && !t.IsInterface && !t.IsAbstract);

        if (restrictToNamespaces?.Length > 0)
        {
            retval = retval.Where(checkType => checkType.Namespace != null && restrictToNamespaces.Contains(checkType.Namespace));
        }

        return retval;
    }

    public static IEnumerable<I> GetImplementingInstances<I>(params string[]? restrictToNamespaces) where I : class
    {
        if (!typeof(I).IsInterface && !typeof(I).IsAbstract) return Enumerable.Empty<I>();

        IEnumerable<I>? retval = DiscoverImplementors<I>(restrictToNamespaces)
            .Select(c => Activator.CreateInstance(c))
            .Where(c => c != null).Select(c => (I)(c!));

        return retval ?? Enumerable.Empty<I>();
    }
}
