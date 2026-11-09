// Seeded violation: a function compared with nullptr, and a lambda turned into a function pointer by unary plus.
#include <cstdint>

namespace kv::rule_7_11_3::bad {

std::int32_t one() { return 1; }

using Fn = std::int32_t (*)();

bool present() { return one != nullptr; }  // seeded

Fn as_pointer() { return +[]() -> std::int32_t { return 2; }; }  // seeded

}  // namespace kv::rule_7_11_3::bad
