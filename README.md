<h1>E-Memoir</h1>
<p>Your own personal e-diary. Write memoirs, access and delete them anytime easily, and the best part, it has a GUI.
How amazing is that. Just open the app and start typing. Plus you can tweak the app as per your liking.</p>

<h3>Extremely intuitive</h3>
<p>The GUI is extremely straight forward and designed keeping the non-techy folks in mind. Everyting is self-explanatory. An program can be run using the .exe file provided. As simple as that.</p>

<hline>
<h3>Easy to use</h3>
<p>Separate tabs are provided for writing, reading and deleting memoirs. The UI looks kinda old and non-fancy and I am working on that, but it works flawlessly.</p>

<ul>
    <li>
        <h4>Write</h4>
        <figure>
        <img src="C:\Users\ayush.kumar.a.singh\Documents\venv\pictures\write tab.jpg" alt="Write Tab">
        <figcaption>Fig.1 - Write Tab</figcaption>
        </figure>
        <p>Select the date you want to write memoir for (by default, the current date is chosen). Click </b>'Preview'</b> to see how the final memoir looks and click <b>'Save'</b> to save the deed. Same memoir can't be saved for the same day, but that can be disabled in the settings, so cheers.</p>
    </li>
    <li>
        <h4>Read</h4>
        <figure>
        <img src="C:\Users\ayush.kumar.a.singh\Documents\venv\pictures\read tab.jpg" alt="Read Tab">
        <figcaption>Fig.2 - Read Tab</figcaption>
        </figure>
        <p>Select the range in terms of date you want to read memoirs for. For a single date, choose the start and end date the same. The memoirs in that date range are shown in the output box below. By default, only the first 20 records are shown to avoid clutter, but that limit can be changed from the settings.</p>
    </li>
    <li>
        <h4>Delete</h4>
        <figure>
        <img src="C:\Users\ayush.kumar.a.singh\Documents\venv\pictures\delete tab.jpg" alt="Delete Tab">
        <figcaption>Fig.1 - Delete Tab</figcaption>
        </figure>
        <p>You can either delete all the memoirs, by selecting <b>'Delete All'</b> or those in a selected date range. Clicking the <b>'Deletion Preview'</b> button shows the records that will be deleted. Click on <b>'Delete Records'</b> to delete. A popup asks if you are sure, selecting 'OK' permanently deletes the records and 'Cancel' cancels deletion. Pretty straight forward. (Moving to Bin is not an option right now but is on my bucket list)</p>
    </li>
    <li>
        <h4>Settings</h4>
        <figure>
        <img src="C:\Users\ayush.kumar.a.singh\Documents\venv\pictures\settings tab.jpg" alt="Settings Tab">
        <figcaption>Fig.1 - Settings Tab</figcaption>
        </figure>
        <p>Tweak the program as per your liking. Options available right now include:
            <ol>
                <li><u>Force Save:</u> Enabling this will allow you to save the same memoir again for the same day. Not sure about the use case though.</li>
                <li><u>Quit after saving the memoir:</u> Enabling this will terminate the program after a memoir is saved. There is a specified delay between saving the memoir and app being closed.</li>
                <li>Delay (in sec):</u> Specify the delay. By default, it is set to 2sec. This is used only when the Quut after saving is enabled.</li>
                <li><u>Date format:</u> The date format used for dates for tagging the memoirs. A single date format is used for the whole memoir. By default, it is set to '28-November-1999' format. If the format is changed, the change is made in all the dates for all the memoirs and the UI as well. Sweet.</li>
                <li><u>Tab Selected color:</u> Color of the tab when it is selected. By default, it is Blue. Only a few other colors are supported at this moment, and inclusion of a simple color picker is on the way.</li>
                <li><u>Max records to display in preview:</u> Max number of records that are displayed in any preview. By default, it is set to 20.</li>
            <ol>
        All the changes take effect on restarting the app. A <b>'Reset settings'</b> button is available to reset the settings back to default. Neat.
        </p>
    </li>
</ul>

<hline>
<h3>Cross Platform</h3>
<p>Will work on Windows/Mac/Linux</p>

<hline>
<p>I worked on this just out of curiosity and my desire to explore PySimpleGUI. The idea is kind of niche and there is a large room for improvement. Tinker with the source code all you want and make something interesting. Ciao </p>

