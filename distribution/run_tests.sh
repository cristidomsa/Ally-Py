#!/bin/sh

PYTHONPATH=$PYTHONPATH:"../components/ally-api"
PYTHONPATH=$PYTHONPATH:"../components/ally-core"
PYTHONPATH=$PYTHONPATH:"../components/ally-core-http"
PYTHONPATH=$PYTHONPATH:"../components/ally-core-sqlalchemy"
PYTHONPATH=$PYTHONPATH:"../components/ally"
PYTHONPATH=$PYTHONPATH:"../components/ally-http"
PYTHONPATH=$PYTHONPATH:"../components/service-cdm"
PYTHONPATH=$PYTHONPATH:"../components/ally-http-asyncore-server"
PYTHONPATH=$PYTHONPATH:"../components/ally-http-mongrel2-server"
PYTHONPATH=$PYTHONPATH:"../components/ally-plugin"
PYTHONPATH=$PYTHONPATH:"../components/ally-indexing"
PYTHONPATH=$PYTHONPATH:"../components/service-assemblage"

PYTHONPATH=$PYTHONPATH:"../plugins/support-sqlalchemy"
PYTHONPATH=$PYTHONPATH:"../plugins/security"
PYTHONPATH=$PYTHONPATH:"../plugins/gui-core"
PYTHONPATH=$PYTHONPATH:"../plugins/support-cdm"
PYTHONPATH=$PYTHONPATH:"../plugins/gateway"
PYTHONPATH=$PYTHONPATH:"../plugins/indexing"
PYTHONPATH=$PYTHONPATH:"../plugins/gui-action"
PYTHONPATH=$PYTHONPATH:"../plugins/internationalization"
PYTHONPATH=$PYTHONPATH:"../plugins/administration"
PYTHONPATH=$PYTHONPATH:"../plugins/security-rbac"
PYTHONPATH=$PYTHONPATH:"../plugins/gateway-acl"

PYTHONPATH=$PYTHONPATH:"../components/service-assemblage"
PYTHONPATH=$PYTHONPATH:"../components/service-gateway"

PYTHONPATH=$PYTHONPATH:"libraries/Babel-1.0dev-py3.2"
PYTHONPATH=$PYTHONPATH:"libraries/SQLAlchemy-0.7.1-py3.2.egg"

export PYTHONPATH
echo $PYTHONPATH

nosetests 	"../plugins/gui-core/__unit_test__" \
		"../components/ally-api/__unit_test__" \
		"../components/ally/__unit_test__" \
		"../components/ally-core-http/__unit_test__" \
		--with-xunit --all-modules

