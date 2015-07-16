<?php
# Database Configuration
define( 'DB_NAME', 'snapshot_henergy' );
define( 'DB_USER', 'henergy' );
define( 'DB_PASSWORD', '8qVBdlZmw7adbQmRGZEZ' );
define( 'DB_HOST', '127.0.0.1' );
define( 'DB_HOST_SLAVE', '127.0.0.1' );
define('DB_CHARSET', 'utf8');
define('DB_COLLATE', 'utf8_unicode_ci');
$table_prefix = 'wp_';

# Security Salts, Keys, Etc
define('AUTH_KEY',         'f!:nlX3Y^UJXqvt-8PlKz8k`6<px_jn{DN7|CuC]+j/+khd(N#-}ES0KZ7wF$dZ&');
define('SECURE_AUTH_KEY',  '1vo5$:MRg{Q6bi%y|yZMY )G2?3];v sd[++=!0t%w2faGc/_@kv|5l/54*2X`Vy');
define('LOGGED_IN_KEY',    'xWbFjcg3g-B|9z)Z^[MoN=.[Cpqnj$T@e!7n&byj5Ytx%%`3;-#vfK-yCh[biXtJ');
define('NONCE_KEY',        '+E<8j;V0SHB-%V[?KWmZw|l^n.FKS1RAUKHaJ4m,Mj0et{pnjN=1-CgD^N5gT9Mt');
define('AUTH_SALT',        '_8-%=^{~x^1m^&+nLs|nXpMu&lEzAEi#C}]d6DrN1AN:p]as9(e4L>NQG|R$J-H~');
define('SECURE_AUTH_SALT', '!o.0n(p kUQWu|`Bhc,;]JH$`(x[5 $N%TQ(4Clc+)j.lG QIty5V!uok  aJso<');
define('LOGGED_IN_SALT',   '(X.L|@m^=P$y)/94HSb@M<hKPSq~aiuJ6IZ?n!K7^J-Tbi65h&M>-7>yIR(<sq^W');
define('NONCE_SALT',       'l*0wkz,LAApXm9<J]dsSxV%YRE!aipa&]dE|sZq=LH0-@0Y6]^:F%/LRb!W,se!q');


# Localized Language Stuff

define( 'WP_CACHE', TRUE );

define( 'WP_AUTO_UPDATE_CORE', false );

define( 'PWP_NAME', 'henergy' );

define( 'FS_METHOD', 'direct' );

define( 'FS_CHMOD_DIR', 0775 );

define( 'FS_CHMOD_FILE', 0664 );

define( 'PWP_ROOT_DIR', '/nas/wp' );

define( 'WPE_APIKEY', 'ca65918fffd479823e6553d19bebfa713dcac6fb' );

define( 'WPE_FOOTER_HTML', "" );

define( 'WPE_CLUSTER_ID', '41354' );

define( 'WPE_CLUSTER_TYPE', 'pod' );

define( 'WPE_ISP', true );

define( 'WPE_BPOD', false );

define( 'WPE_RO_FILESYSTEM', false );

define( 'WPE_LARGEFS_BUCKET', 'largefs.wpengine' );

define( 'WPE_CACHE_TYPE', 'generational' );

define( 'WPE_LBMASTER_IP', '45.33.27.103' );

define( 'WPE_CDN_DISABLE_ALLOWED', true );

define( 'DISALLOW_FILE_EDIT', FALSE );

define( 'DISALLOW_FILE_MODS', FALSE );

define( 'DISABLE_WP_CRON', false );

define( 'WPE_FORCE_SSL_LOGIN', false );

define( 'FORCE_SSL_LOGIN', false );

/*SSLSTART*/ if ( isset($_SERVER['HTTP_X_WPE_SSL']) && $_SERVER['HTTP_X_WPE_SSL'] ) $_SERVER['HTTPS'] = 'on'; /*SSLEND*/

define( 'WPE_EXTERNAL_URL', false );

define( 'WP_POST_REVISIONS', FALSE );

define( 'WPE_WHITELABEL', 'wpengine' );

define( 'WP_TURN_OFF_ADMIN_BAR', false );

define( 'WPE_BETA_TESTER', false );

umask(0002);

$wpe_cdn_uris=array ( );

$wpe_no_cdn_uris=array ( );

$wpe_content_regexs=array ( );

$wpe_all_domains=array ( 0 => 'henergy.wpengine.com', 1 => 'highlandsenergy.biz', 2 => 'highlandsenergy.com', 3 => 'highlandsenergy.net', 4 => 'highlandsenergyservices.biz', 5 => 'highlandsenergyservices.com', 6 => 'highlandsenergyservices.net', 7 => 'www.highlandsenergy.biz', 8 => 'www.highlandsenergy.com', 9 => 'www.highlandsenergy.info', 10 => 'www.highlandsenergy.net', 11 => 'www.highlandsenergyservices.biz', 12 => 'www.highlandsenergyservices.com', 13 => 'www.highlandsenergyservices.net', );

$wpe_varnish_servers=array ( 0 => 'pod-41354', );

$wpe_special_ips=array ( 0 => '45.33.27.103', );

$wpe_ec_servers=array ( );

$wpe_largefs=array ( );

$wpe_netdna_domains=array ( );

$wpe_netdna_domains_secure=array ( );

$wpe_netdna_push_domains=array ( );

$wpe_domain_mappings=array ( );

$memcached_servers=array ( 'default' =>  array ( 0 => 'unix:///tmp/memcached.sock', ), );

define( 'WPE_SFTP_PORT', 2222 );

define( 'WP_SITEURL', 'http://henergy.staging.wpengine.com' );

define( 'WP_HOME', 'http://henergy.staging.wpengine.com' );
define('WPLANG','');

# WP Engine ID


# WP Engine Settings






# That's It. Pencils down
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');
require_once(ABSPATH . 'wp-settings.php');

$_wpe_preamble_path = null; if(false){}
