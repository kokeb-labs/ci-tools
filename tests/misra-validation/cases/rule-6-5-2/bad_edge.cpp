// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_5_2::bad_edge {

static std::int32_t s_count = 0;  // static at namespace scope instead of an unnamed namespace
namespace {
static const std::int32_t kStep = 2;  // redundant static inside the unnamed namespace
}  // namespace
std::int32_t bump() { return s_count + kStep; }

}  // namespace kv::rule_6_5_2::bad_edge
