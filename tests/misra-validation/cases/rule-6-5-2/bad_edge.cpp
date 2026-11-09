// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_5_2::bad_edge {

static std::int32_t s_count = 0;  // seeded
namespace {
static std::int32_t s_step = 2;  // seeded
extern std::int32_t s_shared;  // seeded
std::int32_t s_shared = 1;
}  // namespace
std::int32_t bump() { return s_count + s_step + s_shared; }

}  // namespace kv::rule_6_5_2::bad_edge
