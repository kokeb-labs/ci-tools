// Seeded violation: a function and a lambda silently turned into function pointers.
#include <cstdint>

namespace kv::rule_7_11_3::bad {

std::int32_t one() { return 1; }

using Fn = std::int32_t (*)();

std::int32_t call(Fn f) { return f(); }

bool present() { return one != nullptr; }

std::int32_t use() { return call([]() -> std::int32_t { return 2; }); }

}  // namespace kv::rule_7_11_3::bad
