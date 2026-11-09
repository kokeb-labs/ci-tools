// Seeded violation: system reached through <stdlib.h>, and the availability probe system(nullptr).
#include <stdlib.h>

namespace kv::rule_21_2_3::bad_c_header {

int run(const char* command) { return ::system(command); }

bool shell_available() { return system(nullptr) != 0; }

}  // namespace kv::rule_21_2_3::bad_c_header
