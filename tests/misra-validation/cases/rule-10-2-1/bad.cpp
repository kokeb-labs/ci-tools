// Seeded violation: a scoped enumeration with no fixed underlying type.
namespace kv::rule_10_2_1::bad {

enum class Mode { kIdle, kRun };

Mode next(Mode m) { return (m == Mode::kIdle) ? Mode::kRun : Mode::kIdle; }

}  // namespace kv::rule_10_2_1::bad
