from musicbrainzngs import set_useragent, get_release_group_by_id

class MusicBrainzClient:

    def init_app(self, app, app_name, app_version):
        set_useragent(app_name, app_version)
        app.jinja_env.filters['album_details'] = self.album_details

    def album_details(self, release_group):
        try:
	    api_resp = get_release_group_by_id(release_group, includes=['artists']).get('release-group')
	    resp = dict(title=api_resp.get('title'), 
                    artist=api_resp.get('artist-credit-phrase'),
                    release_date=api_resp.get('first-release-date')[:4])
        except:
            resp = dict(title=None, artist=None, release_date=None)
        return resp

musicbrainz = MusicBrainzClient()
