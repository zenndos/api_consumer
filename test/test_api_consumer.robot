*** Test Cases ***
Test Api Consumer Creates Group On All Hosts
    Given Group Does Not Exist On All Hosts
    When Create Group Request Is Made Towards Consumer
    Then Group Exists On All Hosts

Test Api Consumer Deletes Group On All Hosts
    Given Group Exists On All Hosts
    When Delete Group Request Is Made Towards Consumer
    Then Group Does Not Exist On All Hosts

Test Api Servers Have Same Set Of Objects After Multiple Create Requests
    When Multiple Create Requests Were Made Towards Consumer At The Same Time
    Then Groups Are Equal On All Servers After Short Time


*** Keywords ***
Create Group Request Is Made Towards Consumer
    Wait Until Keyword Succeeds
    ...    40 sec
    ...    1 sec
    ...    Make Create Group Request Towards Consumer    ${TEST_GROUP_ID}    201

Delete Group Request Is Made Towards Consumer
    Wait Until Keyword Succeeds
    ...    40 sec
    ...    1 sec
    ...    Make Delete Group Request Towards Consumer    ${TEST_GROUP_ID}

Multiple Create Requests Were Made Towards Consumer At The Same Time
    FOR    ${i}    IN RANGE    50
        ${handle}=    Run Keyword Async
        ...    Make Create Group Request Towards Consumer    ${i}    any
    END
    Wait Async All    timeout=15

Groups Are Equal On All Servers After Short Time
    Wait Until Keyword Succeeds
    ...    40 sec
    ...    1 sec
    ...    Groups Are Equal On All Servers

Group Exists On All Hosts
    Group Is Created On Host Server    ${HOST_1_SESSION}    ${HOST_1_URL}
    Group Is Created On Host Server    ${HOST_2_SESSION}    ${HOST_2_URL}
    Group Is Created On Host Server    ${HOST_3_SESSION}    ${HOST_3_URL}

Group Does Not Exist On All Hosts
    Group Does Not Exist On Host Server    ${HOST_1_SESSION}    ${HOST_1_URL}
    Group Does Not Exist On Host Server    ${HOST_2_SESSION}    ${HOST_2_URL}
    Group Does Not Exist On Host Server    ${HOST_3_SESSION}    ${HOST_3_URL}

Groups Are Equal On All Servers
    @{group_1}=    Make Get All Groups Request Towards Server And Return Json
    ...    ${HOST_1_SESSION}    ${HOST_1_URL}
    @{group_2}=    Make Get All Groups Request Towards Server And Return Json
    ...    ${HOST_2_SESSION}    ${HOST_2_URL}
    @{group_3}=    Make Get All Groups Request Towards Server And Return Json
    ...    ${HOST_3_SESSION}    ${HOST_3_URL}
    Should Be Equal    ${group_1}    ${group_2}
    Should Be Equal    ${group_2}    ${group_3}

Group Is Created On Host Server
    [Arguments]    ${host_session}    ${host_url}
    ${resp}=    GET On Session
    ...    ${host_session}
    ...    ${host_url}${GROUP_ENDPOINT}${TEST_GROUP_ID}
    ...    expected_status=200

Group Does Not Exist On Host Server
    [Arguments]    ${host_session}    ${host_url}
    ${resp}=    GET On Session
    ...    ${host_session}
    ...    ${host_url}${GROUP_ENDPOINT}${TEST_GROUP_ID}
    ...    expected_status=404

Make Create Group Request Towards Consumer
    [Arguments]    ${group_id}    ${expected_status}
    &{json_body}=    Create Dictionary    groupId    ${group_id}
    ${resp}=    POST On Session
    ...    ${CONSUMER_SESSION}
    ...    ${CONSUMER_URL}${GROUP_ENDPOINT}
    ...    json=&{json_body}
    ...    expected_status=${expected_status}

Make Delete Group Request Towards Consumer
    [Arguments]    ${group_id}
    &{json_body}=    Create Dictionary    groupId    ${group_id}
    ${resp}=    DELETE On Session
    ...    ${CONSUMER_SESSION}
    ...    ${CONSUMER_URL}${GROUP_ENDPOINT}
    ...    json=&{json_body}
    ...    expected_status=200

Make Get All Groups Request Towards Server And Return Json
    [Arguments]    ${host_session}    ${host_url}
    ${resp}=    Get On Session
    ...    ${host_session}
    ...    ${host_url}${ALL_GROUPS_ENDPOINT}
    ...    expected_status=200
    [Return]    ${resp.json()}

Session Is Open Towards All Services
    Create Session    ${HOST_1_SESSION}    ${HOST_1_URL}
    Create Session    ${HOST_2_SESSION}    ${HOST_2_URL}
    Create Session    ${HOST_3_SESSION}    ${HOST_3_URL}
    Create Session    ${CONSUMER_SESSION}    ${CONSUMER_URL}


*** Variables ***
${HOST_1_SESSION}         host_1_session
${HOST_2_SESSION}         host_2_session
${HOST_3_SESSION}         host_3_session
${CONSUMER_SESSION}       cosumer_session
${HOST_1_URL}             http://node01.app.internal.com:5000
${HOST_2_URL}             http://node02.app.internal.com:5000
${HOST_3_URL}             http://node03.app.internal.com:5000
${CONSUMER_URL}           http://192.168.2.4:5001
${GROUP_ENDPOINT}         /v1/group/
${ALL_GROUPS_ENDPOINT}    /v1/group/all/
${TEST_GROUP_ID}          42


*** Settings ***
Library    runKeywordAsync
Library    RequestsLibrary

Suite Setup    Session Is Open Towards All Services
