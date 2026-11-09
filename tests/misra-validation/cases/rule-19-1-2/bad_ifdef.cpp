// Seeded violation: an #ifdef group that is never closed.
#ifdef KV_FEATURE
namespace kv::rule_19_1_2::bad_ifdef {
constexpr int kValue = 1;
}
