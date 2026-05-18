file(GLOB TEST_SOURCES *.cpp)

add_executable(hedging_tests ${TEST_SOURCES})
target_link_libraries(hedging_tests PRIVATE hedging_lib)

add_test(NAME hedging_tests COMMAND hedging_tests)
