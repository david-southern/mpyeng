namespace SSG.Client.Services;

public class SSGEventService
{
    public event EventHandler? FileMenuInvoked;

    public void NotifyFileMenuInvoked(object? sender = null, EventArgs? args = null)
    {
        // Make a temporary copy of the event to avoid possibility of
        // a race condition if the last subscriber unsubscribes
        // immediately after the null check and before the event is raised.
        EventHandler? invokeEvent = FileMenuInvoked;

        // Event will be null if there are no subscribers
        if (invokeEvent != null)
        {
            // Call to raise the event.
            invokeEvent(sender, args ?? EventArgs.Empty);
        }
    }

    public event EventHandler? SettingsInvoked;

    public void NotifySettingsInvoked(object? sender = null, EventArgs? args = null)
    {
        // Make a temporary copy of the event to avoid possibility of
        // a race condition if the last subscriber unsubscribes
        // immediately after the null check and before the event is raised.
        EventHandler? invokeEvent = SettingsInvoked;

        // Event will be null if there are no subscribers
        if (invokeEvent != null)
        {
            // Call to raise the event.
            invokeEvent(sender, args ?? EventArgs.Empty);
        }
    }

}