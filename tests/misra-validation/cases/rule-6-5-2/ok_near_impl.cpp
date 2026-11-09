// Internal linkage through the unnamed namespace, a const object that is internal without static, and a
// static const object in the unnamed namespace (the guideline does not apply to const or constexpr variables).
#include "ok_near_api.hpp"

namespace kv::rule_6_5_2::near {

constexpr std::int32_t kStep = 2;
namespace {
bool small(std::int32_t v) { return v < 100; }
static const std::int32_t kFloor = 1;  // static is redundant here, but the guideline does not apply to const
}  // namespace
std::int32_t bump(std::int32_t v) { return small(v) ? kStep : kFloor; }

}  // namespace kv::rule_6_5_2::near
