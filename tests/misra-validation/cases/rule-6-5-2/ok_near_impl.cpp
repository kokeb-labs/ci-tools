// Internal linkage through the unnamed namespace, and a const object that is internal without static.
#include "ok_near_api.hpp"

namespace kv::rule_6_5_2::near {

constexpr std::int32_t kStep = 2;
namespace {
bool small(std::int32_t v) { return v < 100; }
}  // namespace
std::int32_t bump(std::int32_t v) { return small(v) ? kStep : v; }

}  // namespace kv::rule_6_5_2::near
