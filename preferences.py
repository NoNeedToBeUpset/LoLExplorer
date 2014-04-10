# contains preferences, mainly default settings

# this versionstring may, at some point, actually have some relevance
version = "0.1-git"

# path is a hash, with each entry being a list [defaultvalue, description]
path = {
	'loldir'	: [None, 'LoL Installation Directory'],
	'lolsub'	: ['/RADS/projects/lol_game_client/filearchives', 'Relative archive location'],
	'workdir'	: ['work', 'Working Directory'],
}

startmaximized = True

# info shown in 'About'-popup
about = {
	'title'	:	'LoL Explorer v' + version,
	'msg'	:	'I should probably put some serious-looking info here, but meh.',
}
