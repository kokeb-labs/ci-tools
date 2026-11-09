// Seeded violation: errno set to a computed value and changed by a compound assignment.
#include <cerrno>

namespace kv::rule_22_4_1::bad_compound {

void report(int code) {
  errno = code;
  errno += 1;
}

}  // namespace kv::rule_22_4_1::bad_compound
