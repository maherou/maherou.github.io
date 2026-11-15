# Updating the Scholar highlights

The Publications section on the home page reads `scholar_highlights.json` at the
top of the repo. `fetch_scholar.py` rebuilds that file from the Google Scholar
profile. Run it whenever you want the lists refreshed.

1. **One time only:** open Terminal and run
   `pip3 install -r scripts/requirements.txt`
   (from the repo folder; see step 2 for how to get there).
2. In GitHub Desktop, choose **Repository > Open in Terminal**. That opens
   Terminal in the repo folder. Run:
   `python3 scripts/fetch_scholar.py`
   It prints how many papers it found and what it wrote.
3. Open GitHub Desktop. It will show `scholar_highlights.json` as a changed file.
4. Type a short summary such as "Update Scholar highlights", click
   **Commit to master**, then click **Push origin**.
5. The page updates within a minute or two of the push.

The script makes one request for the profile and then about a dozen more, a
few seconds apart, to get each listed paper's authors. If Google Scholar blocks
any of them (it sometimes shows a "Verifying your request" page to scripts), the
script says so and leaves the existing `scholar_highlights.json` alone. Wait a
while (an hour or a day) and try again.

© 2026 Michael A. Heroux. Code under the MIT License.
