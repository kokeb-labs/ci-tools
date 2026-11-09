// Seeded violation (spelling): the __asm__ spelling of an asm statement.
#include <cstdint>

namespace kv::rule_10_4_1::bad_spelling {

void fence() {
  __asm__ __volatile__("" ::: "memory");  // seeded
}

}  // namespace kv::rule_10_4_1::bad_spelling
