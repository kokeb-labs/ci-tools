// Seeded violation: the <cstdio> remove deleting a file.
#include <cstdio>

namespace kv::rule_30_0_1_algorithm_remove::bad {

bool delete_log() { return std::remove("/tmp/log.txt") == 0; }  // seeded

}  // namespace kv::rule_30_0_1_algorithm_remove::bad
