# NOTE: Mainly those tests are high level/functional black box tests,
#       I don't know if it is possible to have more white box tests,
#       but in general the problem with only functional black box testing
#       is that it can hide internal mistakes.
#       For example the job_list endpoint is accepted with a response code of 200
#       and response data as a list two elements, so what if I change the code to
#       just return something like: `return 200, ['foo', 'bar']` ?
#       Functional black box testing should always come with lower level unit testing
#       whether block or white box.
