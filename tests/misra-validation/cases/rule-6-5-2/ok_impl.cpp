// Compliant: the file-local helper has internal linkage through an anonymous namespace alone.
#include "ok_api.hpp"

namespace kv::rule_6_5_2::ok {

namespace {
bool positive(std::int32_t v) { return v > 0; }
}  // namespace

std::int32_t use(std::int32_t v) { return positive(v) ? v : 0; }

}  // namespace kv::rule_6_5_2::ok
