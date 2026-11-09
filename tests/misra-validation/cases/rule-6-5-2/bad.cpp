// Seeded violation: internal linkage given with static at namespace scope, and static inside an
// anonymous namespace.
#include <cstdint>

namespace kv::rule_6_5_2::bad {

static std::int32_t twice(std::int32_t v) { return v * 2; }  // seeded

namespace {
static std::int32_t thrice(std::int32_t v) { return v * 3; }  // seeded
}  // namespace

std::int32_t use(std::int32_t v) { return twice(v) + thrice(v); }

}  // namespace kv::rule_6_5_2::bad
